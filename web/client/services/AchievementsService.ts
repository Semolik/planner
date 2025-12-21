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
    /**
     * Export Achievements By Year
     * @param year
     * @param kurs
     * @param group
     * @param isMagistracy
     * @param date
     * @param meetingsIds
     * @returns binary Successful Response
     * @throws ApiError
     */
    public static exportAchievementsByYearAchievementsExportGet(
        year: number,
        kurs: number,
        group: string,
        isMagistracy: boolean,
        date: string,
        meetingsIds?: Array<string>,
    ): CancelablePromise<Blob> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/achievements/export',
            query: {
                'year': year,
                'kurs': kurs,
                'group': group,
                'is_magistracy': isMagistracy,
                'date': date,
                'meetings_ids': meetingsIds,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Export Achievements Excel
     * @param year
     * @param participantDate
     * @param participantLink
     * @param meetingsIds
     * @returns any Successful Response
     * @throws ApiError
     */
    public static exportAchievementsExcelAchievementsExportExcelGet(
        year: number,
        participantDate: string,
        participantLink: string,
        meetingsIds?: Array<string>,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/achievements/export-excel',
            query: {
                'year': year,
                'participant_date': participantDate,
                'participant_link': participantLink,
                'meetings_ids': meetingsIds,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
