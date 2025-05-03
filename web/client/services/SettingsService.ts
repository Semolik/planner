/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_set_app_logo_settings_app_logo_put } from '../models/Body_set_app_logo_settings_app_logo_put';
import type { Settings } from '../models/Settings';
import type { SettingsUpdate } from '../models/SettingsUpdate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SettingsService {
    /**
     * Get Settings
     * @returns Settings Successful Response
     * @throws ApiError
     */
    public static getSettingsSettingsGet(): CancelablePromise<Settings> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/settings',
        });
    }
    /**
     * Update Setting
     * @param requestBody
     * @returns Settings Successful Response
     * @throws ApiError
     */
    public static updateSettingSettingsPut(
        requestBody: SettingsUpdate,
    ): CancelablePromise<Settings> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/settings',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Set App Logo
     * @param formData
     * @returns string Successful Response
     * @throws ApiError
     */
    public static setAppLogoSettingsAppLogoPut(
        formData: Body_set_app_logo_settings_app_logo_put,
    ): CancelablePromise<string> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/settings/app_logo',
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
