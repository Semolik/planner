<template>
    <aside>
        <slot name="head" />

        <div class="aside-block" v-for="(block, index) in blocks" :key="index">
            <div class="block-name" v-if="block.name">{{ block.name }}</div>
            <div class="items">
                <template v-if="index === 0">
                    <div
                        class="dropdown-button"
                        :class="{ open: dropdownOpen }"
                        v-if="$viewport.isGreaterOrEquals('lg')"
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
                                :to="{ name: routesNames.tasksAdd }"
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
                    <div v-else class="aside-line">
                        <nuxt-link
                            class="aside-item"
                            :to="{ name: routesNames.tasksAdd }"
                        >
                            <Icon name="material-symbols:add-rounded" />
                            <span> Задача </span>
                        </nuxt-link>
                        <nuxt-link
                            class="aside-item"
                            :to="{ name: routesNames.eventsAdd }"
                        >
                            <Icon name="material-symbols:add-rounded" />
                            <span> Мероприятие </span>
                        </nuxt-link>
                    </div>
                </template>
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
        <div class="aside-block mt-auto">
            <div class="items">
                <div class="aside-item logout" @click="logout">
                    <Icon name="material-symbols:logout-rounded" />
                    Выйти
                </div>
            </div>
        </div>
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
const logout = () => {
    const router = useRouter();
    router.push("/login").then(() => {
        authStore.logout();
    });
};
</script>
<style lang="scss" scoped>
aside {
    display: flex;
    flex-direction: column;

    height: 100%;
    @include lg {
        border-right: 1px solid $border-color;
        width: 280px;
    }
    @include lg(true) {
        width: 100%;
        gap: 10px;
    }
    .spliter {
        height: 1px;
        background-color: $border-color;
    }

    .aside-block {
        display: flex;
        flex-direction: column;
        gap: 10px;
        @include lg {
            padding: 13px;
        }

        .dropdown-button {
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
            @include lg(true) {
                gap: 8px;
            }
            .aside-line {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 5px;
                .aside-item {
                    flex-grow: 1;
                    text-align: center;
                    justify-content: center;
                    gap: 5px;
                }
            }
            .aside-item {
                display: flex;
                padding: 10px;
                text-decoration: none;
                align-items: center;
                gap: 10px;
                border-radius: 10px;
                color: $text-color-secondary;
                border: 1px solid $text-color-secondary;
                cursor: pointer;
                &.logout {
                    &:hover {
                        background-color: $tertiary-bg;
                    }
                }

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
}
</style>
