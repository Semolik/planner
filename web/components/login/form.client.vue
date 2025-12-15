<template>
  <form class="login-modal__body" @submit.prevent="handleSubmit">
    <app-input
        v-model="login"
        label="Имя пользователя"
        placeholder="Введите имя пользователя"
        type="text"
        white
    />
    <app-input
        v-model="password"
        label="Пароль"
        placeholder="Пароль"
        type="password"
        white
    />

    <app-button :active="formValid" type="submit"> Войти</app-button>
    <div ref="social"/>
  </form>
</template>
<script setup>
import {useAuthStore} from "~/stores/auth";
import * as VKID from "@vkid/sdk";
import {AuthService} from '@/client'

const {$toast} = useNuxtApp();
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
  const error = await authStore.login(login.value, password.value);
  if (error) {
    console.log(error);
    $toast.error(HandleOpenApiError(error).message);
  } else {
    console.log('logined');
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
  responseMode: VKID.ConfigResponseMode.Callback,

  codeVerifier: codeVerifier,
  scope: "vkid.personal_info",
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
        .on(VKID.WidgetEvents.ERROR, (err) => {
          console.log('err', err)
          $toast.error("Ошибка авторизации");
        })
        .on(VKID.OAuthListInternalEvents.LOGIN_SUCCESS, async function (payload) {
          try {
            await AuthService.vkCallbackAuthVkCallbackPost({
              code_verifier: codeVerifier,
              ...payload,
            })
            await authStore.getUserData();
          } catch (error) {
            console.log("Ошибка авторизации:", error);
            $toast.error(HandleOpenApiError(error).message);
          } finally {
            const router = useRouter();
            if (router.currentRoute.value.name === "login") {
              router.push("/");
            }
          }
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
