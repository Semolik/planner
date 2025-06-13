/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { State } from './State';
import type { StatePeriod } from './StatePeriod';
import type { UserReadShort } from './UserReadShort';
export type TypedTaskState = {
    id: string;
    user: UserReadShort;
    state: State;
    comment: string;
    period?: (StatePeriod | null);
};

