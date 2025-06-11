/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Institute } from '../models/Institute';
import type { InstituteCreateOrEdit } from '../models/InstituteCreateOrEdit';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class InstitutesService {
    /**
     * Get Institutes
     * @returns Institute Successful Response
     * @throws ApiError
     */
    public static getInstitutesInstitutesGet(): CancelablePromise<Array<Institute>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/institutes',
        });
    }
    /**
     * Create Institute
     * @param requestBody
     * @returns Institute Successful Response
     * @throws ApiError
     */
    public static createInstituteInstitutesPost(
        requestBody: InstituteCreateOrEdit,
    ): CancelablePromise<Institute> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/institutes',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Institute
     * @param instituteId
     * @param requestBody
     * @returns Institute Successful Response
     * @throws ApiError
     */
    public static updateInstituteInstitutesInstituteIdPut(
        instituteId: string,
        requestBody: InstituteCreateOrEdit,
    ): CancelablePromise<Institute> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/institutes/{institute_id}',
            path: {
                'institute_id': instituteId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Institute
     * @param instituteId
     * @returns Institute Successful Response
     * @throws ApiError
     */
    public static getInstituteInstitutesInstituteIdGet(
        instituteId: string,
    ): CancelablePromise<Institute> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/institutes/{institute_id}',
            path: {
                'institute_id': instituteId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Institute
     * @param instituteId
     * @returns void
     * @throws ApiError
     */
    public static deleteInstituteInstitutesInstituteIdDelete(
        instituteId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/institutes/{institute_id}',
            path: {
                'institute_id': instituteId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
