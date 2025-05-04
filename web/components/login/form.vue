<template>
    <div class="login-modal__body">
        <app-input
            v-model="login"
            type="text"
            placeholder="Введите имя пользователя"
            label="Имя пользователя"
            white
        />
        <app-input
            label="Пароль"
            v-model="password"
            type="password"
            placeholder="Пароль"
            white
        />

        <app-button :active="formValid" @click="handleSubmit">
            Войти
        </app-button>
    </div>
</template>
<script setup>
import { useAuthStore } from "~/stores/auth";
const { $toast } = useNuxtApp();
const authStore = useAuthStore();
const emit = defineEmits(["logined"]);

const login = ref("");
const password = ref("");

const email_regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const emailValid = computed(() => {
    return email_regex.test(login.value);
});
const formValid = computed(
    () => login.value.length > 0 && password.value.length > 0
);
const handleSubmit = async () => {
    if (!formValid.value) {
        return;
    }
    var error = await authStore.login(login.value, password.value);
    if (error) {
        $toast.error(HandleOpenApiError(error).message);
        return;
    } else {
        emit("logined");
    }
};
</script>
<style lang="scss" scoped>
.login-modal__body {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    .role-selector {
        display: flex;
        flex-direction: column;
        gap: 3px;
        .label {
            font-size: 14px;
            color: $text-color;
            text-decoration: none;
            margin-left: 3px;
        }
    }
}
</style>
