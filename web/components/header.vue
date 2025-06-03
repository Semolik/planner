<template>
    <header>
        <div class="header-left">
            <nuxt-link class="header_logo" href="/">
                {{ appSettingsStore.settings.app_name }}
            </nuxt-link>
        </div>
        <nav v-if="authStore.logined">
            <ul>
                <div class="logined">
                    <div class="flex items-center gap-2">
                        <nuxt-link class="userName">
                            <div class="name">
                                {{ useFullName(authStore.userData) }}
                            </div>
                        </nuxt-link>
                        <div
                            :class="[
                                'notifications',
                                { 'has-notifications': hasUnreadNotifications },
                            ]"
                            id="notifications"
                            @click="toggleNotificationsOverlay"
                        >
                            <Icon name="material-symbols:notifications" />
                        </div>
                    </div>
                </div>
            </ul>
        </nav>
        <div class="bread-crumb-menu" @click.stop="toggleSidebar">
            <Icon name="ci:hamburger-lg" />
        </div>
        <Teleport
            to="#notifications"
            :disabled="$viewport.isLessOrEquals('sm')"
            v-if="mounted && authStore.logined"
        >
            <div
                :class="[
                    'notifications-overlay',
                    { open: notificationsOverlayOpen },
                    { active: notificationsShown },
                ]"
                ref="notificationsOverlay"
                @click.stop
            >
                <div v-if="notifications.length === 0" class="no-notifications">
                    Нет уведомлений
                </div>
            </div>
        </Teleport>
    </header>
</template>
<script setup>
import { useAppSettingsStore } from "~/stores/app-settings";
import { useAuthStore } from "~/stores/auth";
const authStore = useAuthStore();
const appSettingsStore = useAppSettingsStore();
await appSettingsStore.getSettings();
const hasUnreadNotifications = ref(false);
const notifications = ref([]);
const notificationsOverlayOpen = ref(false);
const notificationsShown = ref(false);
const mounted = ref(false);
const notificationsOverlay = ref(null);
onMounted(() => {
    mounted.value = true;
});
const toggleNotificationsOverlay = () => {
    if (notificationsOverlayOpen.value) {
        notificationsShown.value = false;
        setTimeout(() => {
            notificationsOverlayOpen.value = false;
        }, 200);
    } else {
        notificationsOverlayOpen.value = true;
        setTimeout(() => {
            notificationsShown.value = true;
        }, 0);
    }
};
onClickOutside(notificationsOverlay, (event) => {
    let notificationButton = document.getElementById("notifications");
    if (
        (notificationButton && notificationButton.contains(event.target)) ||
        notificationButton === event.target
    ) {
        return;
    }
    if (notificationsOverlayOpen.value) {
        toggleNotificationsOverlay();
    }
});
</script>
<style lang="scss" scoped>
header {
    color: black;
    user-select: none;
    border-bottom: 1px solid $border-color;
    height: 60px;
    width: 100%;
    position: fixed;
    top: 0;
    z-index: 10;
    .bread-crumb-menu {
        display: none;
        position: absolute;
        right: 0;
        top: 0;
        height: 60px;
        width: 60px;
        line-height: 60px;
        text-align: center;
        font-size: 24px;
        color: black;
        left: 0;

        @include xl(true) {
            display: block;
            width: 100%;
            height: 60px;
            width: 60px;
            font-size: 20px;

            span {
                height: 22px;
                width: 22px;
            }
            @include flex-center;
        }

        @include sm(true) {
            display: block;
        }
    }

    .header-left {
        display: flex;
        align-items: center;
        height: 100%;
        position: absolute;
        left: 0;
        top: 0;
        line-height: 60px;
        font-size: 16px;
        font-weight: 600;

        @include xl(true) {
            width: 100%;
            justify-content: center;
            font-size: 14px;
            padding-left: 0;
            padding-right: 0;
        }
    }

    .header_logo {
        font-size: 16px;
        font-weight: 600;
        color: black;
        text-decoration: none;
        padding-left: 20px;
        padding-right: 20px;
        line-height: 60px;
        height: 60px;
        display: inline-block;
        transition: color 0.1s;

        &:hover {
            color: #0066ff;
            text-decoration: none;
        }
        @include xl(true) {
            width: 100%;
            text-align: center;
            font-size: 14px;
        }
    }

    nav {
        display: inline-block;
        text-align: center;
        position: absolute;
        right: 14px;
        top: 0;
        height: 60px;

        ul {
            text-align: center;
            list-style: none;
            display: inline-flex;
            height: 100%;
            margin: 0;
            .logined {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                .notifications {
                    height: 40px;
                    width: 40px;
                    position: relative;
                    background-color: var(--ui-bg-elevated);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    color: var(--ui-text-muted);
                    .iconify {
                        width: 20px;
                        height: 20px;
                    }

                    &.has-notifications {
                        &::after {
                            content: "";
                            position: absolute;
                            top: 0;
                            right: 0;
                            width: 10px;
                            height: 10px;
                            background-color: #36f;
                            border-radius: 50%;
                        }
                    }
                }
                .notifications {
                    height: 40px;
                    width: 40px;
                    position: relative;
                    background-color: var(--ui-bg-elevated);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    color: var(--ui-text-muted);
                    .iconify {
                        width: 20px;
                        height: 20px;
                    }

                    &.has-notifications {
                        &::after {
                            content: "";
                            position: absolute;
                            top: 0;
                            right: 0;
                            width: 10px;
                            height: 10px;
                            background-color: #36f;
                            border-radius: 50%;
                        }
                    }
                }
                .userName {
                    padding-right: 10px;
                    font-size: 14px;
                    display: block;
                    max-width: 250px;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;

                    @include md(true) {
                        max-width: 150px;
                    }

                    @include sm(true) {
                        display: none;
                    }
                }
            }

            li {
                list-style: none;
                font-size: 100%;
                height: 100%;
                position: relative;
                .divider {
                    background: $border-color;
                    display: block;
                    height: 60%;
                    width: 1px;
                    margin-left: 10px;
                    margin-right: 10px;
                    position: relative;
                    top: 20%;
                }
                .link {
                    align-items: center;
                    text-decoration: none;
                    position: relative;
                    transition: color 0.1s;
                    color: black;
                    display: inline-flex;
                    padding-left: 10px;
                    padding-right: 10px;
                    height: 60px;
                    cursor: pointer;

                    &.blue {
                        transition:
                            box-shadow 0.1s,
                            color 0.1s,
                            background 0.1s;
                        cursor: pointer;
                        text-align: center;
                        white-space: nowrap;
                        border-radius: 8px;
                        font-size: 14px;
                        padding: 0 12px;
                        height: 36px;
                        line-height: 36px;
                        background: #0066ff;
                        color: white;
                        box-shadow:
                            rgba(255, 255, 255, 0) 0 0 0 3px,
                            rgba(0, 102, 255, 0) 0 0 0 4px;
                        margin-top: 13px;

                        &:hover {
                            background: #005ce6;
                        }
                    }
                }
                @include sm(true) {
                    display: none;
                }
            }
        }
    }
}
.notifications-overlay {
    position: absolute;
    z-index: 999;
    background-color: white;
    opacity: 0;
    visibility: hidden;
    transition: all 0.2s ease-in-out;
    opacity: 0;
    &.open {
        visibility: visible;
        right: 0;
        top: 60px;

        @include sm {
            display: flex;
        }
    }
    &.active {
        opacity: 1;
    }
    padding: 10px;
    gap: 5px;
    display: flex;
    overflow-y: auto;
    flex-direction: column;
    @include sm(true) {
        top: 60px;
        right: 100vw;
        width: 100%;
        height: calc(100vh - 60px);
    }
    @include sm {
        display: none;
        border-radius: 15px;
        top: calc(100% + 5px);
        right: 0;

        border: 1px solid $border-color;
        width: 400px;
        max-height: 50vh;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    }
}
</style>
