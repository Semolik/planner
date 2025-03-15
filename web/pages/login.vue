<template>
    <app-form
        headline="Войти в аккаунт"
        @submit.prevent.stop="onSubmit"
        ref="form"
        class="login-form"
        full-height
    >
        <app-input v-model="email" label="Email" required />
        <app-input
            v-model="password"
            label="Пароль"
            required
            type="password"
            :minlength="min_password_length"
            :label-right="{
                text: 'Забыли пароль?',
                to: forgotPasswordUrl,
            }"
        />
        <app-button
            type="submit"
            :active="submitButtonActive"
            class="login-button"
            with-loader
            :loading="submited"
        >
            Войти
        </app-button>
    </app-form>
</template>
<script setup>
import { useAuthStore } from "~~/stores/auth";
const form = ref(null);
const min_password_length = 3;
const authStore = useAuthStore();
const submited = ref(false);
definePageMeta({
    layout: "full-page",
});
const onSubmit = async () => {
    if (!submitButtonActive.value || submited.value) return;
    submited.value = true;
    const error = await authStore.login(email.value, password.value);
    if (error) {
        form.value.showMessage(HandleOpenApiError(error).message);
    } else {
        const router = useRouter();
        router.push("/");
    }
    submited.value = false;
};
const email = ref("");
const password = ref("");
const forgotPasswordUrl = computed(() => {
    return "/forgot-password" + (email.value ? "?email=" + email.value : "");
});
const submitButtonActive = computed(() => {
    return !!(email.value && password.value.length > min_password_length);
});
</script>
<style lang="scss" scoped>
.login-button {
    margin-top: 10px;
}
</style>
