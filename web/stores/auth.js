import { defineStore } from "pinia";
import { AuthService, UsersService, UserRole } from "@/client";

export const useAuthStore = defineStore("auth", {
    state: () => ({
        logined: false,
        userData: null,
    }),
    getters: {
        userRole() {
            return this.userData?.role || null;
        },

        isAdmin() {
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
                await AuthService.authJwtLoginAuthJwtLoginPost({
                    username: username,
                    password: password,
                });
                await this.getUserData();
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
                return error;
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

        async registerRequest(username, password, name, role) {
            this.logined = false;
            try {
                this.userData = await AuthService.registerUserAuthRegisterPost({
                    email: username,
                    password,
                    name,
                    role,
                });
                await this.login(username, password);
            } catch (error) {
                this.resetSavedData();
                return error;
            }
        },
    },
});
