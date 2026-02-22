<template>
    <UApp>
        <NuxtLoadingIndicator />

        <div class="default-layout">
            <template v-if="authStore.logined">
                <app-head v-if="$viewport.isLessThan('lg')" />
                <app-aside v-else :blocks="asideBlocks">
                    <template #head>
                        <app-head />
                    </template>
                </app-aside>
            </template>

            <div id="teleports"/>
            <div :class="['default-layout__content', { padding: !noPadding, 'has-bottom-bar': authStore.logined && $viewport.isLessThan('lg') }]">
                <slot />
            </div>
            <div
                v-if="authStore.logined && $viewport.isLessThan('lg')"
                class="bottom-bar"
            >
                <nuxt-link class="bottom-bar-item" to="/">
                    <Icon name="material-symbols:home-rounded" />
                </nuxt-link>
                <nuxt-link class="bottom-bar-item" to="/tasks">
                    <Icon name="material-symbols:calendar-month" />
                </nuxt-link>
                <nuxt-link class="bottom-bar-item" to="/menu">
                    <Icon
                        name="material-symbols:format-list-bulleted-rounded"
                    />
                </nuxt-link>
            </div>
        </div>
    </UApp>
</template>
<script setup>
import { useAuthStore } from "~/stores/auth";
const { $viewport } = useNuxtApp();
const { noPadding } = defineProps({
    noPadding: {
        type: Boolean,
        default: false,
    },
});
const authStore = useAuthStore();

const { getMenuBlocks, filterBlocksForMobile } = useMenuBlocks();

const asideBlocks = computed(() => {
    const blocks = getMenuBlocks();
    const isMobile = $viewport.isLessThan('lg');
    return filterBlocksForMobile(blocks, isMobile);
});
</script>
<style lang="scss">
.default-layout {
    display: grid;
    grid-template-columns: 280px 1fr;
    grid-template-rows: 1fr auto;
    max-width: 100vw;
    min-height: 100vh;
    height: 100vh;
    overflow-y: auto;
    overflow-x: hidden;
    isolation: isolate;

    & > .aside-fixed {
        grid-row: 1 / span 2;
        grid-column: 1 / 2;
        position: fixed;
        left: 0;
        top: 0;
        width: 280px;
        height: 100vh;
        z-index: 10;
        background: white;
        border-right: 1px solid $border-color;
        display: flex;
        flex-direction: column;
    }
    &__content {
        grid-column: 2 / 3;
        grid-row: 1 / 2;
        min-width: 0;
        width: 100%;
        margin: 0;
        z-index: 0;
        &.padding {
            padding: 13px;
        }
        &.has-bottom-bar {
            padding-bottom: calc(64px + env(safe-area-inset-bottom) + 8px);
        }
        @include lg {
            margin-left: 0;
        }
        @include lg(true) {
            padding: 8px !important;
            grid-column: 1 / -1; // одна колонка на мобильных
        }
    }
    .bottom-bar {
        position: fixed;
        left: 0;
        right: 0;
        bottom: 0;
        background: white;
        border-top: 1px solid $border-color;
        z-index: 20;
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        padding: 8px calc(8px + env(safe-area-inset-left)) calc(8px + env(safe-area-inset-bottom)) calc(8px + env(safe-area-inset-right));

        .bottom-bar-item {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 10px 8px;
            background: $secondary-bg;
            border: 1px solid $border-color;
            border-radius: 8px;
            .iconify {
                width: 20px;
                height: 20px;
            }
            &.router-link-exact-active {
                color: white;
                background-color: black;
                border-color: transparent;

                .iconify {
                    color: white;
                }
            }
        }
    }
}
</style>