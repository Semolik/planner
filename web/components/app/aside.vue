<template>
    <aside>
        <div class="head">
            <nuxt-link class="header_logo" href="/">
                <div class="logo" v-if="appSettingsStore.settings.app_logo">
                    <img :src="appSettingsStore.settings.app_logo" alt="Logo" />
                </div>
                <div class="name">
                    {{ appSettingsStore.settings.app_name }}
                </div>
            </nuxt-link>
        </div>

        <div class="aside-block" v-for="(block, index) in blocks" :key="index">
            <div class="block-name" v-if="block.name">{{ block.name }}</div>
            <div class="items">
                <div
                    class="dropdown-button"
                    :class="{ open: dropdownOpen }"
                    v-if="index === 0"
                    @click="dropdownOpen = !dropdownOpen"
                    v-auto-animate
                >
                    <div class="button-content">
                        Создать
                        <Icon name="i-lucide-chevron-down" />
                    </div>
                    <div class="links" v-if="dropdownOpen" @click.stop>
                        <nuxt-link
                            class="link"
                            @click.stop.prevent="dropdownOpen = false"
                        >
                            задачу
                        </nuxt-link>
                        <nuxt-link
                            class="link"
                            :to="{ name: routesNames.eventsAdd }"
                            @click.stop.prevent="dropdownOpen = false"
                        >
                            мероприятие
                        </nuxt-link>
                    </div>
                </div>

                <nuxt-link
                    class="aside-item"
                    v-for="item in block.items"
                    :key="item.path"
                    :to="{
                        name: item.path,
                    }"
                >
                    <Icon :name="item.icon" />
                    <span>
                        {{ item.name }}
                    </span>
                </nuxt-link>
            </div>
        </div>
        <slot name="bottom" />
    </aside>
</template>
<script setup>
import { useAppSettingsStore } from "~/stores/app-settings";
import { routesNames } from "@typed-router";
import { useAuthStore } from "~/stores/auth";

const authStore = useAuthStore();
const dropdownOpen = ref(false);

const appSettingsStore = useAppSettingsStore();
await appSettingsStore.getSettings();
const { blocks } = defineProps({
    blocks: {
        type: Array,
        default: () => [],
    },
});
const mounted = ref(false);
onMounted(() => {
    mounted.value = true;
});
const items = [
    {
        label: "Settings",
        icon: "i-lucide-cog",
    },
];
</script>
<style lang="scss" scoped>
aside {
    display: flex;
    flex-direction: column;
    width: 280px;

    border-right: 1px solid $border-color;
    height: 100%;

    .spliter {
        height: 1px;
        background-color: $border-color;
    }
    .head {
        display: flex;
        align-items: center;
        padding: 13px;

        gap: 10px;
        border-bottom: 1px solid $border-color;

        .header_logo {
            display: flex;
            align-items: center;
            text-decoration: none;
            color: $text-color-secondary;

            .logo {
                width: 30px;
                height: 30px;
                img {
                    width: 100%;
                    height: 100%;
                    object-fit: contain;
                }
            }
            .name {
                font-size: 18px;
                font-weight: bold;
                margin-left: 10px;
            }
        }
    }
    .aside-block {
        padding: 13px;
        display: flex;
        flex-direction: column;
        gap: 10px;

        .dropdown-button {
            // background-color: black;
            border: 1px solid black;
            color: black;
            padding: 8px;
            border-radius: 10px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            cursor: pointer;
            user-select: none;

            .button-content {
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            &.open .iconify {
                transform: rotate(180deg);
            }
            .iconify {
                width: 20px;
                height: 20px;
                color: black;
            }
            .links {
                display: grid;
                grid-template-columns: 1fr 1fr;

                gap: 5px;

                .link {
                    border: 1px solid black;
                    color: black;
                    text-align: center;
                    font-size: 14px;
                    padding: 3px 5px;
                    text-decoration: none;
                    border-radius: 5px;

                    &:hover {
                        background-color: $tertiary-bg;
                    }
                }
            }
        }

        .items {
            display: flex;
            flex-direction: column;
            gap: 5px;
            .aside-item {
                display: flex;
                padding: 10px;
                text-decoration: none;
                align-items: center;
                gap: 10px;
                border-radius: 10px;
                color: $text-color-secondary;
                border: 1px solid $text-color-secondary;

                &.router-link-exact-active {
                    color: white;
                    background-color: black;
                    border-color: transparent;

                    .iconify {
                        color: white;
                    }
                }

                .iconify {
                    width: 20px;
                    height: 20px;
                    color: $text-color-secondary;
                }
                .name {
                    color: $text-color-secondary;
                    margin-bottom: 10px;
                    word-wrap: break-word;
                    overflow-wrap: anywhere;
                }
            }
        }
    }
    @include sm(true) {
        & {
            width: 100%;
            padding: 5px;
        }
    }
}
</style>
