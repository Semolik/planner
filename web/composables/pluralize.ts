export const usePluralize = (number: number, words: string[]): string => {
    const pluralize = (num: number, wordList: string[]): string => {
        const cases = [2, 0, 1, 1, 1, 2];
        return wordList[
            num % 100 > 4 && num % 100 < 20
                ? 2
                : cases[num % 10 < 5 ? num % 10 : 5]
        ];
    };
    return pluralize(number, words);
};

