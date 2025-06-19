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
     * Получить статистику пользователей за указанный период.
     * Период задается датами начала и конца.
     * @param periodStart
     * @param periodEnd
     * @returns StatsUser Successful Response
     * @throws ApiError
     */
    public static getStatisticsStatisticsGet(
        periodStart: string,
        periodEnd: string,
    ): CancelablePromise<Array<StatsUser>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/statistics',
            query: {
                'period_start': periodStart,
                'period_end': periodEnd,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
