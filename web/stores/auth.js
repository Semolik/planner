import { defineStore } from "pinia";
import { AuthService, UsersService } from "@/client";

export const useAuthStore = defineStore({
    id: "auth",
    state: () => ({
        logined: false,
        userData: null,
    }),
    getters: {
        isSuperuser() {
            return this.userData?.is_superuser;
        },
    },
    actions: {
        resetSavedData() {
            this.logined = false;
            this.userData = null;
        },
        async logout() {
            try {
                await AuthService.authJwtLogoutAuthJwtLogoutPost();
            } catch (error) {}
            this.resetSavedData();
        },
        async login(username, password) {
            this.logined = false;
            try {
                this.userData = await AuthService.authJwtLoginAuthJwtLoginPost({
                    username: username,
                    password: password,
                });
                this.logined = true;
            } catch (error) {
                this.resetSavedData();
                return error;
            }
        },
        async getUserData() {
            try {
                this.userData = await UsersService.usersCurrentUserUsersMeGet();
                this.logined = true;
            } catch (error) {
                console.log(error);
                this.resetSavedData();
            }
        },
        async updateProfile(data) {
            try {
                this.userData = await UsersService.updateUserMeUsersMePut({
                    ...this.userData,
                    ...data,
                });
            } catch (error) {
                return error;
            }
        },
        async registerRequest(username, password, name) {
            this.logined = false;
            try {
                this.userData = await AuthService.registerUserAuthRegisterPost({
                    username,
                    password,
                    name,
                });
                this.logined = true;
            } catch (error) {
                this.resetSavedData();
                return error;
            }
        },
    },
});
