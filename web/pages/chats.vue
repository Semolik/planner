<template>
    <app-form full-height headline="Настройки чатов">
        <div class="flex gap-2" v-if="status.vk_token_set">
            <app-input
                model-value="установлен"
                label="Статус токена ВКонтакте"
                white
                readonly
            />
            <app-button
                :active="!removeToken"
                @click="
                    () => {
                        removeToken = true;
                    }
                "
                red
                class="remove-button"
            >
                <Icon name="material-symbols:delete" />
            </app-button>
        </div>
        <app-input
            v-model="token"
            label="Токен ВКонтакте"
            required
            white
            v-else
        />
        <template v-if="status.vk_token_set">
            <UCheckbox
                v-model="vk_chat_photographers_enabled"
                label="Чат фотографов"
                variant="card"
                color="neutral"
            />
            <template v-if="status.vk_chat_photographers_enabled">
                <div class="chat" v-if="status.photographers_chat">
                    <div class="name">
                        {{ status.photographers_chat.name }}
                    </div>
                    <div class="members-count">
                        {{ status.photographers_chat.members_count }}
                        {{
                            usePluralize(
                                status.photographers_chat.members_count,
                                ["участник", "участника", "участников"]
                            )
                        }}
                    </div>
                </div>
                <div class="chat empty" v-else>Чат не подключен</div>
            </template>
            <UCheckbox
                v-model="vk_chat_copywriters_enabled"
                label="Чат копирайтеров"
                variant="card"
                color="neutral"
            />
            <template v-if="status.vk_chat_copywriters_enabled">
                <div class="chat" v-if="status.copywriters_chat">
                    <div class="name">
                        {{ status.copywriters_chat.name }}
                    </div>
                    <div class="members-count">
                        {{ status.copywriters_chat.members_count }}
                        {{
                            usePluralize(
                                status.copywriters_chat.members_count,
                                ["участник", "участника", "участников"]
                            )
                        }}
                    </div>
                </div>
                <div class="chat empty" v-else>Чат не подключен</div></template
            >
            <UCheckbox
                v-model="vk_chat_designers_enabled"
                label="Чат дизайнеров"
                variant="card"
                color="neutral"
            />
            <template v-if="status.vk_chat_designers_enabled">
                <div class="chat" v-if="status.designers_chat">
                    <div class="name">
                        {{ status.designers_chat.name }}
                    </div>
                    <div class="members-count">
                        {{ status.designers_chat.members_count }}
                        {{
                            usePluralize(status.designers_chat.members_count, [
                                "участник",
                                "участника",
                                "участников",
                            ])
                        }}
                    </div>
                </div>
                <div class="chat empty" v-else>Чат не подключен</div>
            </template>
        </template>
        <app-button :active="saveButtonActive" @click="handleSave">
            Сохранить
        </app-button>
    </app-form>
</template>
<script setup>
import { VkService } from "~/client";
useSeoMeta({
    title: "Чаты",
});
definePageMeta({
    middleware: ["admin"],
});
const status = ref(await VkService.getStatusVkSettingsGet());
const token = ref("");
const removeToken = ref(false);
const vk_chat_photographers_enabled = ref(
    status.value.vk_chat_photographers_enabled
);
const vk_chat_copywriters_enabled = ref(
    status.value.vk_chat_copywriters_enabled
);
const vk_chat_designers_enabled = ref(status.value.vk_chat_designers_enabled);
const saveButtonActive = computed(() => {
    return (
        token.value.length > 0 ||
        removeToken.value ||
        vk_chat_photographers_enabled.value !==
            status.value.vk_chat_photographers_enabled ||
        vk_chat_copywriters_enabled.value !==
            status.value.vk_chat_copywriters_enabled ||
        vk_chat_designers_enabled.value !==
            status.value.vk_chat_designers_enabled
    );
});
const handleSave = async () => {
    if (!saveButtonActive.value) return;
    if (removeToken.value) {
        await VkService.deleteTokenVkTokenDelete();
        status.value.vk_token_set = false;
        removeToken.value = false;
        return;
    }
    if (token.value) {
        await VkService.setTokenVkTokenPost({ token: token.value });
        status.value.vk_token_set = true;
    }
    status.value = await VkService.updateSettingsVkSettingsPut({
        vk_chat_photographers_enabled: vk_chat_photographers_enabled.value,
        vk_chat_copywriters_enabled: vk_chat_copywriters_enabled.value,
        vk_chat_designers_enabled: vk_chat_designers_enabled.value,
    });
    token.value = "";
};
</script>
<style scoped lang="scss">
.remove-button {
    width: 40px;
    height: 40px;
    margin-top: auto;
}
.chat {
    display: flex;
    padding: 10px;
    justify-content: space-between;
    border: 1px solid $border-color;
    background-color: white;
    border-radius: 8px;

    &.empty {
        justify-content: center;
        color: $text-color-secondary;
    }

    .name {
        font-weight: 600;
        font-size: 16px;
    }
    .members-count {
        font-size: 14px;
        color: $text-color-secondary;
    }
}
</style>
