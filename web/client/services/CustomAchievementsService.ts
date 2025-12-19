/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AchievementCreate } from '../models/AchievementCreate';
import type { AchievementRead } from '../models/AchievementRead';
import type { AchievementUpdate } from '../models/AchievementUpdate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class CustomAchievementsService {
    /**
     * Create Custom Achievement
     * @param requestBody
     * @returns AchievementRead Successful Response
     * @throws ApiError
     */
    public static createCustomAchievementCustomAchievementsPost(
        requestBody: AchievementCreate,
    ): CancelablePromise<AchievementRead> {
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
     * @returns AchievementRead Successful Response
     * @throws ApiError
     */
    public static updateCustomAchievementCustomAchievementsCustomAchievementIdPut(
        customAchievementId: string,
        requestBody: AchievementUpdate,
    ): CancelablePromise<AchievementRead> {
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
