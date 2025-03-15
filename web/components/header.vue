<template>
    <header>
        <nuxt-link to="/" class="home">
            <img src="/logo.png" />
            <div class="title">АИС объединение фотографов</div>
        </nuxt-link>
        <div class="links">
            <nuxt-link to="/login" class="home"> Войти </nuxt-link>
        </div>
    </header>
</template>
<style lang="scss" scoped>
header {
    box-shadow: rgba(0, 0, 0, 0.075) 0 1px;
    height: 60px;
    width: 100%;
    display: flex;
    justify-content: space-between;

    .home {
        padding: 5px;
        display: flex;
        text-decoration: none;
        gap: 5px;
        color: black;
        img {
            object-fit: cover;
            height: 100%;
        }
        .title {
            font-size: 20px;
            @include flex-center;
        }
    }
    .links {
        display: flex;
        gap: 5px;
        padding: 10px;
        a {
            background-color: $cambridge-blue;
            padding: 10px 20px;
            @include flex-center;
            border-radius: 10px;
            color: $text-color;

            &:hover {
                background-color: $viridian;
            }
        }
    }
}
</style>
