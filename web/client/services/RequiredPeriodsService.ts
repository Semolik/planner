/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreateOrUpdatePeriodRequest } from '../models/CreateOrUpdatePeriodRequest';
import type { RequiredPeriod } from '../models/RequiredPeriod';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class RequiredPeriodsService {
    /**
     * Get Required Periods
     * @returns RequiredPeriod Successful Response
     * @throws ApiError
     */
    public static getRequiredPeriodsRequiredPeriodsGet(): CancelablePromise<Array<RequiredPeriod>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/required-periods',
        });
    }
    /**
     * Create Required Period
     * @param requestBody
     * @returns RequiredPeriod Successful Response
     * @throws ApiError
     */
    public static createRequiredPeriodRequiredPeriodsPost(
        requestBody: CreateOrUpdatePeriodRequest,
    ): CancelablePromise<RequiredPeriod> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/required-periods',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Required Period
     * @param periodId
     * @returns RequiredPeriod Successful Response
     * @throws ApiError
     */
    public static getRequiredPeriodRequiredPeriodsPeriodIdGet(
        periodId: string,
    ): CancelablePromise<RequiredPeriod> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/required-periods/{period_id}',
            path: {
                'period_id': periodId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Required Period
     * @param periodId
     * @param requestBody
     * @returns RequiredPeriod Successful Response
     * @throws ApiError
     */
    public static updateRequiredPeriodRequiredPeriodsPeriodIdPut(
        periodId: string,
        requestBody: CreateOrUpdatePeriodRequest,
    ): CancelablePromise<RequiredPeriod> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/required-periods/{period_id}',
            path: {
                'period_id': periodId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Required Period
     * @param periodId
     * @returns void
     * @throws ApiError
     */
    public static deleteRequiredPeriodRequiredPeriodsPeriodIdDelete(
        periodId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/required-periods/{period_id}',
            path: {
                'period_id': periodId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
