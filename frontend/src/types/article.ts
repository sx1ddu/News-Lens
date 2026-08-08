export interface Prediction {
    label: string;
    confidence: number;
}

export interface Article {
    title: string;
    summary: string;
    source: string;
    url: string;
    image: string | null;
    published: string | null;

    bias: Prediction;
    stance: Prediction | null;
}

export interface StanceGroup {
    count: number;
    consensus: string;
    articles: Article[];
}

export interface SearchResponse {
    topic: string;
    total_articles: number;
    processed_articles: number;
    failed_articles: number;

    articles: Article[];

    bias_groups: {
        left: Article[];
        center: Article[];
        right: Article[];
    };

    stance_groups: {
        supports: StanceGroup;
        neutral: StanceGroup;
        critical: StanceGroup;
    } | null;

    stance_unavailable_reason: string | null;
}
