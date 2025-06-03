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
        isUser() {
            return this.userData?.role === UserRole.USER;
        },
        // Проверка, является ли пользователь администратором
        isAdmin() {
            return this.userData?.role === UserRole.ADMIN;
        },

        // Проверка, является ли пользователь модератором или выше
        isModerator() {
            return this.userData?.role === UserRole.MODERATOR;
        },

        // Проверка, является ли пользователь организатором или выше
        isOrganizer() {
            return this.userData?.role === UserRole.ORGANIZER;
        },
        isModeratorOrAdmin() {
            return this.isModerator || this.isAdmin;
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
