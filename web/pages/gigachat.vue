<template>
    <app-form full-height headline="GigaChat">
        <template v-if="status.gigachat_token_set">
            <div class="token-info">
                <div class="token-status">
                    <div class="status-badge">
                        <Icon name="material-symbols:check-circle" />
                        Токен установлен
                    </div>
                </div>
                <app-button
                    :active="!removeToken"
                    red
                    class="remove-button"
                    @click="removeToken = true"
                >
                    <Icon name="material-symbols:delete" />
                </app-button>
            </div>

            <div v-if="loading && !balance" class="loading">
                <Icon name="eos-icons:loading" />
                Загрузка баланса...
            </div>
            <template v-else-if="balance">
                <div class="balance-card">
                    <div v-if="loading" class="loading-indicator">
                        <Icon name="eos-icons:loading" />
                    </div>
                    <div class="balance-header">
                        <h3>Баланс токенов</h3>
                        <div class="balance-stats">
                            <div class="stat">
                                <div class="stat-label">Всего</div>
                                <div class="stat-value">{{ formatNumber(balance.total_tokens) }}</div>
                            </div>
                            <div class="stat">
                                <div class="stat-label">Использовано</div>
                                <div class="stat-value used">{{ formatNumber(balance.used_tokens) }}</div>
                            </div>
                            <div class="stat">
                                <div class="stat-label">Осталось</div>
                                <div class="stat-value remaining">{{ formatNumber(balance.remaining_tokens) }}</div>
                            </div>
                        </div>
                    </div>

                    <div class="progress-section">
                        <div class="progress-label">
                            <span>Использование: {{ balance.usage_percentage.toFixed(2) }}%</span>
                        </div>
                         <div class="progress-visual">
                            <div
                                class="used-bar"
                                :style="{ width: balance.usage_percentage + '%' }"
                            ></div>
                        </div>
                    </div>


                </div>

                <app-button
                    class="refresh-button"
                    @click="refreshBalance"
                    active
                >
                    <Icon name="material-symbols:refresh" />
                    Обновить
                </app-button>
            </template>
        </template>
        <template v-else>
            <app-input
                v-model="token"
                label="Токен авторизации"
                type="password"
                placeholder="Введите ваш GigaChat токен"
                required
                white
            />
        </template>

        <app-button
            :active="token.length > 0 || removeToken"
            @click="handleSave"
            :loading="settingToken"
        >
            Сохранить
        </app-button>

        <UModal
            v-model:open="removeToken"
            title="Удаление токена"
        >
            <template #body>
                Вы уверены, что хотите удалить токен GigaChat?

            </template>
            <template #footer>

                    <app-button
                        @click="removeToken = false" active
                    >
                        Отмена
                    </app-button>
                    <app-button
                        red
                        active
                        @click="handleRemoveToken"
                    >
                        Удалить
                    </app-button>

            </template>
        </UModal>
    </app-form>
</template>

<script setup>
import { GigachatService } from "~/client";
import { HandleOpenApiError } from "~/composables/handleErrors";

useSeoMeta({
    title: "GigaChat",
});

definePageMeta({
    middleware: ["admin"],
});

const { $toast } = useNuxtApp();

const token = ref("");
const removeToken = ref(false);
const loading = ref(false);
const settingToken = ref(false);
const balance = ref(null);

const loadBalance = async () => {
    if (!balance.value) {
        loading.value = true;
    }
    try {
        return await GigachatService.getBalanceGigachatBalanceGet();
    } catch (error) {
        console.error("Failed to load balance:", error);
        $toast.error(HandleOpenApiError(error).message);
        return null;
    } finally {

        loading.value = false;
    }
};

const loadStatus = async () => {
    try {
        const statusData = await GigachatService.getStatusGigachatStatusGet();
        if (statusData.gigachat_token_set) {
            balance.value = await loadBalance();
        } else {
            balance.value = null;
        }
        return statusData;
    } catch (error) {
        console.error("Failed to load status:", error);
        $toast.error(HandleOpenApiError(error).message);
        return { gigachat_token_set: false };
    }
};

const status = ref(await loadStatus());

const refreshBalance = async () => {
    try {
        balance.value = await GigachatService.getBalanceGigachatBalanceGet();
    } catch (error) {
        console.error("Failed to refresh balance:", error);
        $toast.error(HandleOpenApiError(error).message);
    }
};

const handleSave = async () => {
    if (removeToken.value) {
        try {
            await GigachatService.deleteTokenGigachatTokenDelete();
            $toast.success("Токен удален");
            removeToken.value = false;
            status.value = await loadStatus();
        } catch (error) {
            console.error("Failed to remove token:", error);
            $toast.error(HandleOpenApiError(error).message);
        }
        return;
    }

    if (token.value) {
        settingToken.value = true;
        try {
            await GigachatService.setTokenGigachatTokenPost({ token: token.value });
            token.value = "";
            $toast.success("Токен установлен");
            status.value = await loadStatus();
        } catch (error) {
            console.error("Failed to set token:", error);
            $toast.error(HandleOpenApiError(error).message);
            status.value = await loadStatus();
        } finally {
            settingToken.value = false;
        }
    }
};

const handleRemoveToken = async () => {
    await handleSave();
};

const formatNumber = (num) => {
    return new Intl.NumberFormat("ru-RU").format(Math.round(num));
};
</script>

<style scoped lang="scss">
.token-info {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 16px;
    background-color: $primary-bg;
    border: 1px solid #e5e7eb;

    border-radius: 8px;


    .token-status {
        flex: 1;

        .status-badge {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #059669;
            font-weight: 600;
            font-size: 14px;

            svg {
                font-size: 20px;
            }
        }
    }

    .remove-button {
        flex-shrink: 0;
        width: 44px;
        height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;

        svg {
            font-size: 20px;
        }
    }
}

.loading {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 32px;
    color: #6b7280;
    font-size: 16px;

    svg {
        font-size: 24px;
        animation: spin 1s linear infinite;
    }
}

@keyframes spin {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}

.balance-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 24px;
    position: relative;

    .loading-indicator {
        position: absolute;
        top: 16px;
        right: 16px;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #f3f4f6;
        border-radius: 50%;
        font-size: 24px;
        animation: spin 1s linear infinite;
        color: #6b7280;
        z-index: 10;

    }

    .balance-header {


        h3 {
            margin: 0 0 16px 0;
            font-size: 18px;
            font-weight: 600;
            color: #1f2937;
        }

        .balance-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 16px;

            .stat {
                padding: 12px;
                background-color: #f3f4f6;
                border-radius: 6px;

                .stat-label {
                    font-size: 12px;
                    color: #6b7280;
                    margin-bottom: 4px;
                    text-transform: uppercase;
                    font-weight: 600;
                }

                .stat-value {
                    font-size: 18px;
                    font-weight: 700;
                    color: #1f2937;

                    &.used {
                        color: #dc2626;
                    }

                    &.remaining {
                        color: #059669;
                    }
                }
            }
        }
    }

    .progress-section {

        .progress-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 14px;
            color: #6b7280;
            font-weight: 500;
        }
    }

    .progress-visual {
        width: 100%;
        height: 8px;
        background-color: #e5e7eb;
        border-radius: 4px;
        overflow: hidden;
        margin-top: 12px;

        .used-bar {
            height: 100%;
            background: linear-gradient(90deg, #ef4444, #dc2626);
            border-radius: 4px;
            transition: width 0.3s ease;
        }
    }
}

.refresh-button {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;

    svg {
        font-size: 18px;
    }
}

.modal-content {
    padding: 20px;

    p {
        margin: 0 0 12px 0;
        color: #1f2937;
        line-height: 1.5;

        &.warning {
            color: #dc2626;
            font-size: 14px;
        }
    }
}

.modal-footer {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    padding: 16px 0;

    button {
        flex: 1;
    }
}
</style>

