<script setup lang="ts">
import { UsersService } from "~/client";
import type { UserReadWithEmail } from "~/client";

const { $toast } = useNuxtApp();

const props = defineProps<{
    user: UserReadWithEmail | null;
    open: boolean;
}>();

const emit = defineEmits<{
    (e: "update:open", value: boolean): void;
    (e: "deleted", userId: string): void;
}>();

const isLoading = ref(false);

const close = () => emit("update:open", false);

const confirmDelete = async () => {
    if (!props.user) return;

    try {
        isLoading.value = true;
        await UsersService.deleteUserUsersUserIdDelete(props.user.id);

        $toast.success("Пользователь успешно удален");
        emit("deleted", props.user.id);
        close();
    } catch (error) {
        $toast.error(HandleOpenApiError(error).message);
    } finally {
        isLoading.value = false;
    }
};
</script>

<template>
    <UModal
        v-if="user"
        :open="open"
        title="Удаление пользователя"
        @update:open="emit('update:open', $event)"
    >
        <template #body>
            <p>
                Вы уверены, что хотите удалить пользователя
                <strong>{{ useFullName(user) }} </strong>? Это действие нельзя
                будет отменить.
            </p>
            <div class="grid grid-cols-2 gap-2 mt-4">
                <app-button active :disabled="isLoading" @click="close">
                    Отмена
                </app-button>
                <app-button
                    active
                    red
                    :loading="isLoading"
                    @click="confirmDelete"
                >
                    Удалить
                </app-button>
            </div>
        </template>
    </UModal>
</template>
