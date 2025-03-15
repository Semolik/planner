<template>
    <aside>
        <div class="aside-block">
            <div class="app-name">AR CMS</div>
            <div class="items">
                <nuxt-link
                    class="aside-item"
                    v-for="item in items"
                    :to="item.path"
                >
                    <Icon :name="item.icon" />
                    <span>{{ item.name }}</span>
                </nuxt-link>
            </div>
        </div>
        <div class="aside-block splitted" v-if="currentAppStore.currentApp">
            <div class="current-app">
                <div class="name">{{ currentAppStore.currentApp.name }}</div>
                <div class="items">
                    <nuxt-link
                        class="aside-item"
                        :to="`/apps/${currentAppStore.currentApp.id}`"
                    >
                        <Icon name="material-symbols:layers" />
                        <span>Объекты</span>
                    </nuxt-link>
                    <nuxt-link
                        class="aside-item"
                        :to="`/apps/${currentAppStore.currentApp.id}/users`"
                    >
                        <Icon name="material-symbols:person" />
                        <span>Пользователи</span>
                    </nuxt-link>
                    <nuxt-link
                        class="aside-item"
                        :to="`/apps/${currentAppStore.currentApp.id}/settings`"
                        v-if="currentAppStore.canChange"
                    >
                        <Icon name="material-symbols:settings" />
                        <span>Настройки</span>
                    </nuxt-link>
                </div>
            </div>
        </div>
        <div class="aside-block account">
            <div class="account-block items">
                <nuxt-link class="aside-item login" to="/profile">
                    <Icon name="material-symbols:account-circle" />
                    <span>{{ authStore.userData.name }}</span>
                </nuxt-link>
                <div class="aside-item logout" @click="logout">
                    <Icon name="material-symbols:logout" />
                    <span>Выйти</span>
                </div>
            </div>
        </div>
    </aside>
</template>
<script setup>
import { useAuthStore } from "~~/stores/auth";
import { useCurrentAppStore } from "@/stores/current-app";
const currentAppStore = useCurrentAppStore();
const authStore = useAuthStore();
const items = [
    {
        name: "Приложения",
        path: "/",
        icon: "material-symbols:apps",
    },
];
if (authStore.isSuperuser) {
    items.push({
        name: "Институты",
        path: "/faculties",
        icon: "cil:education",
    });
    items.push({
        name: "Пользователи",
        path: "/users",
        icon: "cil:people",
    });
}
const logout = async () => {
    const router = useRouter();
    router.push("/login").then(async () => {
        await authStore.logout();
    });
};
</script>
<style lang="scss" scoped>
aside {
    background-color: $secondary-bg;
    display: flex;
    flex-direction: column;
    width: 280px;
    gap: 10px;
    border-right: 1px solid $border-color;
    @include md(true) {
        width: min-content;
        padding: 10px;

        .aside-item span {
            display: none;
        }
        .app-name {
            display: none;
        }
    }
    @include sm(true) {
        padding: 5px;
    }
    .aside-block {
        padding: 8px;
        display: flex;
        flex-direction: column;

        @include md(true) {
            padding: 0;
            padding-top: 10px;
        }
        &.splitted:not(:where(:first, :last)) {
            border-top: 2px solid $border-color;
        }

        &.account {
            margin-top: auto;
        }
    }

    .app-name {
        font-weight: 600;
        color: $text-color;
        font-size: 1.1rem;
        // margin-left: 5px;
        margin-bottom: 10px;
        padding: 8px;
    }

    .aside-item {
        display: flex;
        padding: 10px;
        text-decoration: none;
        align-items: center;
        gap: 10px;
        border-radius: 10px;
        color: $text-color-secondary;
        @include md(true) {
            @include flex-center;
        }

        &.router-link-exact-active {
            color: $text-color;
            background-color: white;
            svg {
                color: $accent;
            }
        }

        svg {
            width: 25px;
            height: 25px;
            color: $text-color-secondary;
        }
    }
    .items {
        display: flex;
        flex-direction: column;
        gap: 5px;
    }
    .spliter {
        height: 1px;
        background-color: $border-color;
    }
    .current-app {
        display: flex;
        flex-direction: column;
        gap: 10px;

        padding-bottom: 0px;
        @include md {
            padding: 10px;
        }
        .name {
            color: $text-color-secondary;
            margin-bottom: 10px;
            word-wrap: break-word;
            overflow-wrap: anywhere;
            @include md(true) {
                display: none;
            }
        }
    }
    .account-block {
        gap: 10px;

        .aside-item {
            cursor: pointer;
            &:hover {
                background-color: $tertiary-bg;
            }
            background-color: white;
        }
    }
}
</style>
