/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SearchResponse } from '../models/SearchResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SearchService {
    /**
     * Search
     * Поиск по задачам, мероприятиям, группам и пользователям
     *
     * - **q**: Поисковый запрос (минимум 2 символа)
     * - **limit**: Максимум результатов для каждого типа (по умолчанию 50, максимум 100)
     * @param q Поисковый запрос
     * @param limit Максимум результатов
     * @returns SearchResponse Successful Response
     * @throws ApiError
     */
    public static searchSearchGet(
        q: string,
        limit: number = 50,
    ): CancelablePromise<SearchResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/search',
            query: {
                'q': q,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
