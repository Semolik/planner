/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CalendarItem } from '../models/CalendarItem';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class CalendarService {
    /**
     * Get Calendar
     * @param dateFrom
     * @param dateTo
     * @returns CalendarItem Successful Response
     * @throws ApiError
     */
    public static getCalendarCalendarGet(
        dateFrom: string = '2026-02-16',
        dateTo: string = '2026-02-22',
    ): CancelablePromise<Record<string, Array<CalendarItem>>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/calendar',
            query: {
                'date_from': dateFrom,
                'date_to': dateTo,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
