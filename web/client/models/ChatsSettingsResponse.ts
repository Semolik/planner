/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Chat } from './Chat';
export type ChatsSettingsResponse = {
    vk_chat_photographers_enabled: boolean;
    vk_chat_copywriters_enabled: boolean;
    vk_chat_designers_enabled: boolean;
    photographers_chat: (Chat | null);
    copywriters_chat: (Chat | null);
    designers_chat: (Chat | null);
    vk_token_set: boolean;
};

