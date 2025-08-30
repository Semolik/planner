<template>
    <app-form full-height headline="Вход в личный кабинет" center-mobile>
        <login-form @logined="onLogin" />
    </app-form>
</template>
<script setup>
const onLogin = () => {
    const router = useRouter();
    router.push("/");
};
</script>
