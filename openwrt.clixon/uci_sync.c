/* uci_sync.c - Version Final con soporte de Gateway via Description */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdarg.h>
#include <time.h>

/* CONFIGURACIÓN */
#define DB_PATH "/usr/local/var/clixon/candidate_db"
#define HASH_PATH "/var/run/uci_sync.hash"
#define LOG_PATH "/tmp/uci_sync.log"
#define CHECK_INTERVAL 5

/* ESTRUCTURAS DE DATOS */
struct iface_info {
    char name[64];
    char ip[64];
    char netmask[64];
};

struct route_info {
    char target[64];
    char device[64];
    char gateway[64];
};

/* --- UTILIDADES --- */

// Calcula un hash simple para detectar cambios en el archivo de configuración
static unsigned long simple_hash(const char *buf, size_t len) {
    unsigned long hash = 5381;
    for (size_t i = 0; i < len; ++i)
        hash = ((hash << 5) + hash) + (unsigned char)buf[i];
    return hash;
}

// Función de logging para escribir eventos en el archivo de registro
static void log_msg(const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    FILE *log = fopen(LOG_PATH, "a");
    if (log) {
        time_t t = time(NULL);
        char ts[64];
        strftime(ts, sizeof(ts), "%Y-%m-%d %H:%M:%S", localtime(&t));
        fprintf(log, "[%s] ", ts);
        vfprintf(log, fmt, ap);
        fprintf(log, "\n");
        fclose(log);
    }
    va_end(ap);
}

// Lee un archivo completo y lo carga en memoria
static char *read_file(const char *path, size_t *out_len) {
    FILE *f = fopen(path, "rb");
    if (!f) return NULL;
    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    rewind(f);
    if (sz < 0) { fclose(f); return NULL; }
    
    char *buf = malloc(sz + 1);
    if (!buf) { fclose(f); return NULL; }
    
    if (fread(buf, 1, sz, f) != (size_t)sz) { free(buf); fclose(f); return NULL; }
    buf[sz] = '\0';
    *out_len = (size_t)sz;
    fclose(f);
    return buf;
}

/* Parser de etiquetas XML robusto (ignora namespaces) */
static char *extract_tag(const char *start, const char *end, const char *tag) {
    const char *p = start;
    while (p < end) {
        const char *found = strstr(p, tag);
        if (!found) return NULL;
        
        char prev = *(found - 1);
        if (prev != '<' && prev != ':') { p = found + 1; continue; }
        
        const char *gt = strchr(found, '>');
        if (!gt || gt >= end) return NULL;
        
        char close_search[128];
        snprintf(close_search, sizeof(close_search), "%s>", tag);
        const char *c = strstr(gt, close_search);
        if (!c || c >= end) return NULL;
        
        const char *content_start = gt + 1;
        const char *content_end = c;
        while (content_end > content_start && *content_end != '<') { content_end--; }
        
        size_t len = content_end - content_start;
        if (len <= 0) { p = gt + 1; continue; }
        
        char *res = malloc(len + 1);
        if (!res) return NULL;
        memcpy(res, content_start, len);
        res[len] = '\0';
        return res;
    }
    return NULL;
}

/* --- LÓGICA UCI --- */

// Aplica la configuración de una interfaz a UCI
static void apply_interface_uci(const struct iface_info *i) {
    if (!i->name[0] || !i->ip[0] || !i->netmask[0]) return;
    char cmd[512];
    
    // Elimina la configuración anterior y crea la nueva
    snprintf(cmd, sizeof(cmd), "uci delete network.%s 2>/dev/null || true", i->name); system(cmd);
    snprintf(cmd, sizeof(cmd), "uci set network.%s=interface", i->name); system(cmd);
    snprintf(cmd, sizeof(cmd), "uci set network.%s.device='%s'", i->name, i->name); system(cmd);
    snprintf(cmd, sizeof(cmd), "uci set network.%s.proto='static'", i->name); system(cmd);
    snprintf(cmd, sizeof(cmd), "uci set network.%s.ipaddr='%s'", i->name, i->ip); system(cmd);
    snprintf(cmd, sizeof(cmd), "uci set network.%s.netmask='%s'", i->name, i->netmask); system(cmd);
    
    log_msg("Interface %s configured.", i->name);
}

// Aplica la configuración de una ruta estática a UCI
static void apply_route_uci(const struct route_info *r) {
    if (!r->target[0]) return;
    char cmd[512];
    
    system("uci add network route");
    snprintf(cmd, sizeof(cmd), "uci set network.@route[-1].target='%s'", r->target); system(cmd);
    
    if (r->device[0]) {
        snprintf(cmd, sizeof(cmd), "uci set network.@route[-1].interface='%s'", r->device); system(cmd);
    }
    if (r->gateway[0]) {
        snprintf(cmd, sizeof(cmd), "uci set network.@route[-1].gateway='%s'", r->gateway); system(cmd);
    }
    system("uci set network.@route[-1].unicast='true'");
    
    log_msg("Route Added -> Target: %s | Dev: %s | GW: %s", r->target, r->device, r->gateway);
}

/* --- PROCESAMIENTO --- */

// Extrae y procesa la información de las interfaces desde el XML
static void process_interfaces(const char *buf, size_t len) {
    const char *p = buf;
    const char *end = buf + len;
    
    while (p < end) {
        const char *found = strstr(p, "interface");
        if (!found) break;
        if (*(found-1) != '<' && *(found-1) != ':') { p = found + 1; continue; }
        
        const char *gt = strchr(found, '>'); if (!gt) { p = found + 1; continue; }
        const char *close = strstr(gt, "interface>"); if (!close) { p = gt + 1; continue; }
        
        size_t blen = close - p + 15;
        char *block = malloc(blen);
        if (block) {
            int copy_len = (int)(close - gt);
            if (copy_len > blen) copy_len = blen - 1;
            strncpy(block, gt + 1, copy_len);
            block[copy_len] = '\0';
            
            struct iface_info info = {0};
            char *name = extract_tag(block, block + strlen(block), "name");
            
            if (name) {
                strncpy(info.name, name, sizeof(info.name)-1);
                char *addr_blk = extract_tag(block, block + strlen(block), "address");
                
                if (addr_blk) {
                    char *ip = extract_tag(addr_blk, addr_blk + strlen(addr_blk), "ip");
                    char *mask = extract_tag(addr_blk, addr_blk + strlen(addr_blk), "netmask");
                    
                    if (ip) { strncpy(info.ip, ip, sizeof(info.ip)-1); free(ip); }
                    if (mask) { strncpy(info.netmask, mask, sizeof(info.netmask)-1); free(mask); }
                    free(addr_blk);
                }
                free(name);
                apply_interface_uci(&info);
            }
            free(block);
        }
        p = close + 10;
    }
}

// Extrae y procesa la información de enrutamiento desde el XML
static void process_routes(const char *buf, size_t len) {
    // Limpiar rutas anteriores
    system("while uci -q delete network.@route[0]; do :; done");
    
    const char *p = buf;
    const char *end = buf + len;
    
    while (p < end) {
        const char *found = strstr(p, "route");
        if (!found) break;
        if (*(found-1) != '<' && *(found-1) != ':') { p = found + 1; continue; }
        
        const char *gt = strchr(found, '>'); if (!gt) { p = found + 1; continue; }
        const char *close = strstr(gt, "route>"); if (!close) { p = gt + 1; continue; }
        
        size_t content_len = close - gt;
        char *block = malloc(content_len + 1);
        if (block) {
            strncpy(block, gt + 1, content_len);
            block[content_len] = '\0';
            
            struct route_info info = {0};
            char *dest = extract_tag(block, block + strlen(block), "destination-prefix");
            char *nh_block = extract_tag(block, block + strlen(block), "next-hop");
            
            if (nh_block) {
                char *iface = extract_tag(nh_block, nh_block + strlen(nh_block), "outgoing-interface");
                if (iface) {
                    strncpy(info.device, iface, sizeof(info.device)-1);
                    free(iface);
                }
                free(nh_block);
            }
            
            char *desc = extract_tag(block, block + strlen(block), "description");
            if (desc) {
                // Hack: extrae la IP de la puerta de enlace de la descripción "GW:x.x.x.x"
                if (strncmp(desc, "GW:", 3) == 0) {
                    strncpy(info.gateway, desc + 3, sizeof(info.gateway)-1);
                }
                free(desc);
            }
            
            if (dest && (info.device[0] || info.gateway[0])) {
                strncpy(info.target, dest, sizeof(info.target)-1);
                apply_route_uci(&info);
            }
            
            if (dest) free(dest);
            free(block);
        }
        p = close + 1;
    }
}

/* --- FUNCIÓN PRINCIPAL --- */
int main(int argc, char **argv) {
    log_msg("uci_sync (gateway mod) started.");
    
    unsigned long last_hash = 0;
    FILE *f_hash = fopen(HASH_PATH, "r");
    if (f_hash) { 
        if (fscanf(f_hash, "%lu", &last_hash) != 1) last_hash = 0; 
        fclose(f_hash); 
    }
    
    // Bucle infinito: comprueba cambios en la base de datos de Clixon cada X segundos
    while (1) {
        size_t len = 0;
        char *buf = read_file(DB_PATH, &len);
        
        if (buf) {
            unsigned long current_hash = simple_hash(buf, len);
            
            if (current_hash != last_hash) {
                if (last_hash != 0) log_msg("Change detected.");
                
                process_interfaces(buf, len);
                process_routes(buf, len);
                
                // Aplica los cambios de UCI
                system("uci commit network");
                system("/etc/init.d/network reload");
                log_msg("Reload complete.");
                
                last_hash = current_hash;
                f_hash = fopen(HASH_PATH, "w");
                if (f_hash) { 
                    fprintf(f_hash, "%lu", last_hash); 
                    fclose(f_hash); 
                }
            }
            free(buf);
        }
        sleep(CHECK_INTERVAL);
    }
    return 0;
}
