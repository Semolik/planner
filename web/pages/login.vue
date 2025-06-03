<template>
    <app-form full-height headline="Вход в личный кабинет">
        <login-form @logined="onLogin" />
    </app-form>
</template>
<script setup>
const onLogin = () => {
    console.log("onLogin");
    const router = useRouter();
    router.push("/");
};
</script>
