/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CustomAchievementCreate } from '../models/CustomAchievementCreate';
import type { CustomAchievementRead } from '../models/CustomAchievementRead';
import type { CustomAchievementUpdate } from '../models/CustomAchievementUpdate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class CustomAchievementsService {
    /**
     * Create Custom Achievement
     * @param requestBody
     * @returns CustomAchievementRead Successful Response
     * @throws ApiError
     */
    public static createCustomAchievementCustomAchievementsPost(
        requestBody: CustomAchievementCreate,
    ): CancelablePromise<CustomAchievementRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/custom-achievements',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Custom Achievement
     * @param customAchievementId
     * @param requestBody
     * @returns CustomAchievementRead Successful Response
     * @throws ApiError
     */
    public static updateCustomAchievementCustomAchievementsCustomAchievementIdPut(
        customAchievementId: string,
        requestBody: CustomAchievementUpdate,
    ): CancelablePromise<CustomAchievementRead> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/custom-achievements/{custom_achievement_id}',
            path: {
                'custom_achievement_id': customAchievementId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Custom Achievement
     * @param customAchievementId
     * @returns void
     * @throws ApiError
     */
    public static deleteCustomAchievementCustomAchievementsCustomAchievementIdDelete(
        customAchievementId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/custom-achievements/{custom_achievement_id}',
            path: {
                'custom_achievement_id': customAchievementId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
