include $(TOPDIR)/rules.mk

PKG_NAME:=uci_sync
PKG_RELEASE:=1

include $(INCLUDE_DIR)/package.mk

define Package/uci_sync
  SECTION:=utils
  CATEGORY:=Utilities
  TITLE:=UCI Sync Tool
endef

define Package/uci_sync/description
  A daemon to synchronize Clixon YANG databases to OpenWrt UCI.
endef

define Build/Compile
	$(TARGET_CC) $(TARGET_CFLAGS) $(TARGET_LDFLAGS) \
	$(PKG_BUILD_DIR)/uci_sync.c -o $(PKG_BUILD_DIR)/uci_sync
endef

define Package/uci_sync/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/uci_sync $(1)/usr/bin/
endef

$(eval $(call BuildPackage,uci_sync))
