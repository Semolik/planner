/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_auth_jwt_login_auth_jwt_login_post } from '../models/Body_auth_jwt_login_auth_jwt_login_post';
import type { UserCreate } from '../models/UserCreate';
import type { UserRead } from '../models/UserRead';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AuthService {
    /**
     * Auth:Jwt.Login
     * @param formData
     * @returns any Successful Response
     * @throws ApiError
     */
    public static authJwtLoginAuthJwtLoginPost(
        formData: Body_auth_jwt_login_auth_jwt_login_post,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/auth/jwt/login',
            formData: formData,
            mediaType: 'application/x-www-form-urlencoded',
            errors: {
                400: `Bad Request`,
                422: `Validation Error`,
            },
        });
    }
    /**
     * Auth:Jwt.Logout
     * @returns any Successful Response
     * @throws ApiError
     */
    public static authJwtLogoutAuthJwtLogoutPost(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/auth/jwt/logout',
            errors: {
                401: `Missing token or inactive user.`,
            },
        });
    }
    /**
     * Register User
     * @param requestBody
     * @returns UserRead Successful Response
     * @throws ApiError
     */
    public static registerUserAuthRegisterPost(
        requestBody: UserCreate,
    ): CancelablePromise<UserRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/auth/register',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
