<template>
    <form class="login-modal__body" @submit.prevent="handleSubmit">
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

        <app-button :active="formValid" type="submit"> Войти </app-button>
        <div ref="social"></div>
    </form>
</template>
<script setup>
import { useAuthStore } from "~/stores/auth";
import * as VKID from "@vkid/sdk";
const { $toast } = useNuxtApp();
const authStore = useAuthStore();
const emit = defineEmits(["logined"]);
const runtimeConfig = useRuntimeConfig();
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
const codeVerifier =
    localStorage.getItem("core_verifier") ||
    Math.random().toString(36).substring(2, 128) +
        Math.random().toString(36).substring(2, 128);
localStorage.setItem("core_verifier", codeVerifier);

VKID.Config.init({
    app: runtimeConfig.public.vkAppId,
    redirectUrl: `${window.location.origin}/vk-auth`,

    codeVerifier: codeVerifier,
    scope: "email phone vkid.personal_info", // Список прав доступа, которые нужны приложению.
});

const oAuth = new VKID.OAuthList();
const social = ref(null);
watch(social, (newValue) => {
    if (newValue) {
        oAuth
            .render({
                container: social.value,
                oauthList: ["vkid"],
            })
            .on(VKID.WidgetEvents.ERROR, () => {
                $toast.error("Ошибка авторизации");
            })
            .on(VKID.OAuthListInternalEvents.LOGIN_SUCCESS, function (payload) {
                AuthService.vkCallbackAuthVkCallbackPost({
                    code_verifier: codeVerifier,
                    ...Object.fromEntries(payload.entries()),
                })
                    .then(async (response) => {
                        await authStore.getUserData();
                    })
                    .catch((error) => {
                        console.error("Ошибка авторизации:", error);
                        $toast.error(HandleOpenApiError(error).message);
                    })
                    .finally(() => {
                        const router = useRouter();
                        if (router.currentRoute.value.name === "login") {
                            router.push("/");
                        }
                    });
            });
    }
});
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
