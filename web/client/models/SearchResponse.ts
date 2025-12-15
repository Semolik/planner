/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SearchResultItem } from './SearchResultItem';
/**
 * Ответ от поиска
 */
export type SearchResponse = {
    query: string;
    results: Array<SearchResultItem>;
    total: number;
};

