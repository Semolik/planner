/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { StatsUser } from '../models/StatsUser';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class StatisticsService {
    /**
     * Get Statistics
     * @param periodId
     * @returns StatsUser Successful Response
     * @throws ApiError
     */
    public static getStatisticsStatisticsGet(
        periodId: string,
    ): CancelablePromise<Array<StatsUser>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/statistics',
            query: {
                'period_id': periodId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get User Statistics
     * @param userId
     * @param periodId
     * @returns StatsUser Successful Response
     * @throws ApiError
     */
    public static getUserStatisticsStatisticsUserIdGet(
        userId: string,
        periodId: string,
    ): CancelablePromise<StatsUser> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/statistics/{user_id}',
            path: {
                'user_id': userId,
            },
            query: {
                'period_id': periodId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
