<template>
    <div class="head">
        <nuxt-link class="header_logo" href="/">
            {{ appSettingsStore.settings.app_name }}
        </nuxt-link>
    </div>
</template>
<script setup>
const appSettingsStore = useAppSettingsStore();
await appSettingsStore.getSettings();
</script>
<style lang="scss" scoped>
.head {
    display: flex;
    align-items: center;
    padding: 13px;
    height: 60px;
    gap: 10px;
    border-bottom: 1px solid $border-color;

    .header_logo {
        display: flex;

        text-decoration: none;
        color: $text-color-secondary;
        font-size: 18px;
        font-weight: bold;
    }
}
</style>
