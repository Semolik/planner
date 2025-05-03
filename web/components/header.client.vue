<template>
    <header>
        <div class="header-left">
            <nuxt-link class="header_logo" href="/">
                IF-ELSE-AGGREGATOR
            </nuxt-link>
        </div>
    </header>
</template>

<style lang="scss" scoped>
header {
    color: black;
    user-select: none;
    border-bottom: 1px solid $border-color;
    height: 60px;
    width: 100%;
    position: fixed;
    top: 0;
    z-index: 10;
    .bread-crumb-menu {
        display: none;
        position: absolute;
        right: 0;
        top: 0;
        height: 60px;
        width: 60px;
        line-height: 60px;
        text-align: center;
        font-size: 24px;
        color: black;
        left: 0;

        @include xl(true) {
            display: block;
            width: 100%;
            height: 60px;
            width: 60px;
            font-size: 20px;

            span {
                height: 22px;
                width: 22px;
            }
            @include flex-center;
        }

        @include sm(true) {
            display: block;
        }
    }

    .header-left {
        display: flex;
        align-items: center;
        height: 100%;
        position: absolute;
        left: 0;
        top: 0;
        line-height: 60px;
        font-size: 16px;
        font-weight: 600;

        @include xl(true) {
            width: 100%;
            justify-content: center;
            font-size: 14px;
            padding-left: 0;
            padding-right: 0;
        }
    }

    .header_logo {
        font-size: 16px;
        font-weight: 600;
        color: black;
        text-decoration: none;
        padding-left: 20px;
        padding-right: 20px;
        line-height: 60px;
        height: 60px;
        display: inline-block;
        transition: color 0.1s;

        &:hover {
            color: #0066ff;
            text-decoration: none;
        }
        @include xl(true) {
            width: 100%;
            text-align: center;
            font-size: 14px;
        }
    }

    nav {
        display: inline-block;
        text-align: center;
        position: absolute;
        right: 14px;
        top: 0;
        height: 60px;

        ul {
            text-align: center;
            list-style: none;
            display: inline-flex;
            height: 100%;
            margin: 0;
            .logined {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                .userName {
                    padding-right: 10px;
                    font-size: 14px;
                    display: block;
                    max-width: 250px;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;

                    @include md(true) {
                        max-width: 150px;
                    }

                    @include sm(true) {
                        display: none;
                    }
                }
            }

            li {
                list-style: none;
                font-size: 100%;
                height: 100%;
                position: relative;
                .divider {
                    background: $border-color;
                    display: block;
                    height: 60%;
                    width: 1px;
                    margin-left: 10px;
                    margin-right: 10px;
                    position: relative;
                    top: 20%;
                }
                .link {
                    align-items: center;
                    text-decoration: none;
                    position: relative;
                    transition: color 0.1s;
                    color: black;
                    display: inline-flex;
                    padding-left: 10px;
                    padding-right: 10px;
                    height: 60px;
                    cursor: pointer;

                    &.blue {
                        transition:
                            box-shadow 0.1s,
                            color 0.1s,
                            background 0.1s;
                        cursor: pointer;
                        text-align: center;
                        white-space: nowrap;
                        border-radius: 8px;
                        font-size: 14px;
                        padding: 0 12px;
                        height: 36px;
                        line-height: 36px;
                        background: #0066ff;
                        color: white;
                        box-shadow:
                            rgba(255, 255, 255, 0) 0 0 0 3px,
                            rgba(0, 102, 255, 0) 0 0 0 4px;
                        margin-top: 13px;

                        &:hover {
                            background: #005ce6;
                        }
                    }
                }
                @include sm(true) {
                    display: none;
                }
            }
        }
    }
}
</style>
