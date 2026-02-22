import { defineStore } from "pinia";
import { AuthService, UsersService, UserRole } from "@/client";
import type { UserReadWithEmail } from "@/client";

export const useAuthStore = defineStore("auth", {
    state: () => ({
        logined: false,
        userData: null as UserReadWithEmail | null,
        redirectTo: null as string | null,
    }),
    getters: {


        isAdmin(): boolean {
            return this.userData ? this.userData.is_superuser : false;
        },
    },
    actions: {
        resetSavedData() {
            this.logined = false;
            this.userData = null;
        },
        setRedirectTo(url: string) {
            this.redirectTo = url;
        },
        clearRedirectTo() {
            this.redirectTo = null;
        },
        async logout() {
            try {
                await AuthService.authJwtLogoutAuthJwtLogoutPost();
            } catch (error) {}
            this.resetSavedData();
        },
        async login(username: string, password: string) {
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
        async updateProfile(data: Partial<UserReadWithEmail>) {
            try {
                this.userData = await UsersService.updateUserMeUsersMePut({
                    ...this.userData,
                    ...data,
                });
            } catch (error) {
                return error;
            }
        },

        async registerRequest(username: string, password: string, name: string, role: UserRole) {
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

