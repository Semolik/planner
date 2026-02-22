import { routesNames } from "@typed-router";
import { useAuthStore } from "~/stores/auth";
import type { UserReadWithEmail } from "@/client";

export const useMenuBlocks = () => {
    const authStore = useAuthStore();
    const userData = computed(() => authStore.userData as UserReadWithEmail | null);

    const getMenuBlocks = () => {
        const blocks: any[] = [
            {
                name: null,
                items: [
                    {
                        name: "Главная",
                        path: routesNames.index,
                        icon: "material-symbols:home-rounded",
                    },
                    {
                        name: "Профиль",
                        path: routesNames.usersMe,
                        icon: "material-symbols:person-rounded",
                    },
                    {
                        name: "Мои задачи",
                        icon: "material-symbols:task-alt-rounded",
                        path: routesNames.tasksMy,
                    }
                ],
            },
            {
                name: "Мероприятия",
                items: [
                    {
                        name: "Мероприятия и задачи",
                        path: routesNames.tasks,
                        icon: "material-symbols:calendar-month",
                    },
                    {
                        name: "Группы мероприятий",
                        path: routesNames.eventsGroups,
                        icon: "material-symbols:folder-rounded",
                    },
                ],
            },
            {
                name: "Отчеты",
                items: [
                    {
                        name: "Моя статистика",
                        icon: "material-symbols:bar-chart-rounded",
                        path: routesNames.statisticsMe,
                    },
                    {
                        name: "Планерки",
                        path: routesNames.meetings,
                        icon: "material-symbols:meeting-room-rounded",
                        mobile: false,
                    },
                    {
                        name: "ПГАС",
                        path: routesNames.usersUserIdAchievements,
                        params: {
                            user_id: userData.value?.id || '',
                        },
                        icon: "material-symbols:attach-money-rounded",
                        mobile: false,
                    },
                ],
            },
        ];

        if (authStore.isAdmin) {
            blocks.push({
                name: "Администрирование",
                items: [
                    {
                        name: "Пользователи",
                        path: routesNames.users,
                        icon: "material-symbols:person-rounded",
                        mobile: false,
                    },
                    {
                        name: "Дни рождения",
                        path: routesNames.birthdays,
                        icon: "material-symbols:cake-rounded",
                    },
                    {
                        name: "Статистика",
                        icon: "material-symbols:analytics-outline-rounded",
                        path: routesNames.statistics,
                        mobile: false,
                    },
                    {
                        name: "Отчетные периоды",
                        icon: "material-symbols:date-range-rounded",
                        path: routesNames.periods,
                        mobile: false,
                    },
                    {
                        name: "Институты",
                        path: routesNames.institutes,
                        icon: "material-symbols:account-balance-rounded",
                        mobile: false,
                    },
                    {
                        name: "Привязанные чаты",
                        icon: "material-symbols:chat-rounded",
                        path: routesNames.chats,
                        mobile: false,
                    },
                    {
                        name: "GigaChat",
                        icon: "material-symbols:smart-toy-rounded",
                        path: routesNames.gigachat,
                        mobile: false,
                    },
                    {
                        name: "Настройки",
                        icon: "material-symbols:settings-rounded",
                        path: routesNames.settings,
                        mobile: false,
                    },
                ],
            });
        }

        return blocks;
    };

    const filterBlocksForMobile = (blocks: any[], isMobile: boolean) => {
        if (!isMobile) {
            return blocks;
        }

        return blocks.map((block: any) => ({
            ...block,
            items: block.items.filter((item: any) => item.mobile !== false)
        })).filter((block: any) => block.items.length > 0);
    };

    return {
        getMenuBlocks,
        filterBlocksForMobile,
    };
};

