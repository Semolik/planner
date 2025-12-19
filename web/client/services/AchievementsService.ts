/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AchievementRead } from '../models/AchievementRead';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AchievementsService {
    /**
     * Get Achievements By Year
     * @param year
     * @param onlyCustom
     * @returns AchievementRead Successful Response
     * @throws ApiError
     */
    public static getAchievementsByYearAchievementsGet(
        year: number,
        onlyCustom: boolean = false,
    ): CancelablePromise<Array<AchievementRead>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/achievements',
            query: {
                'year': year,
                'only_custom': onlyCustom,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
