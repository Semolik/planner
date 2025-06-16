<template>
    <app-form full-height headline="Настройки чатов">
        <div class="flex gap-2" v-if="status">
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
const status = ref(await VkService.getTokenStatusVkTokenStatusGet());
const token = ref("");
const removeToken = ref(false);
const saveButtonActive = computed(() => {
    return token.value.length > 0 || removeToken.value;
});
const handleSave = async () => {
    if (!saveButtonActive.value) return;
    if (removeToken.value) {
        await VkService.deleteTokenVkTokenDelete();
        status.value = false;
        removeToken.value = false;
        return;
    }
    await VkService.setTokenVkTokenPost({ token: token.value });
    status.value = true;
    token.value = "";
};
</script>
<style scoped>
.remove-button {
    width: 40px;
    height: 40px;
    margin-top: auto;
}
</style>
