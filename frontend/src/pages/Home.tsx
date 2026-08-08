import { useState } from "react";

import Logo from "../components/Logo";
import SearchBar from "../components/SearchBar";
import SearchButton from "../components/SearchButton";
import EmptyState from "../components/EmptyState";
import LoadingSpinner from "../components/LoadingSpinner";
import PerspectiveOverview from "../components/PerspectiveOverview";
import PerspectiveSection from "../components/PerspectiveSection";

import { searchNews } from "../services/api";
import type { SearchResponse } from "../types/article";

export default function Home() {

    const [query, setQuery] = useState("");

    const [result, setResult] = useState<SearchResponse | null>(null);

    const [loading, setLoading] = useState(false);

    const [error, setError] = useState<string | null>(null);

    const handleSearch = async () => {

        if (!query.trim()) return;

        setLoading(true);
        setError(null);

        try {

            const data = await searchNews(query);

            setResult(data);

        }

        catch (err) {

            console.error(err);

            setError("Failed to fetch articles. Please try again.");

            setResult(null);

        }

        finally {

            setLoading(false);

        }

    };

    const articles = result?.articles ?? [];

    return (

        <main
            className="
                min-h-screen
                bg-gradient-to-br
                from-slate-50
                via-blue-50
                to-cyan-50
                px-6
                py-10
            "
        >

            <div className="max-w-7xl mx-auto space-y-10">

                <Logo />

                <div className="flex gap-4">

                    <SearchBar
                        value={query}
                        onChange={setQuery}
                    />

                    <SearchButton
                        onClick={handleSearch}
                    />

                </div>

                {loading && (
                    <LoadingSpinner />
                )}

                {!loading && error && (
                    <div className="text-red-600 font-medium">
                        {error}
                    </div>
                )}

                {!loading && !error && articles.length === 0 && (
                    <EmptyState />
                )}

                {!loading && !error && result && articles.length > 0 && (

                    <>

                        <div className="text-gray-600 text-lg font-medium">

                            Showing{" "}

                            <span className="font-bold">
                                {result.processed_articles}
                            </span>{" "}

                            of {result.total_articles} articles

                            {result.failed_articles > 0 && (
                                <span className="text-gray-400">
                                    {" "}({result.failed_articles} could not be processed)
                                </span>
                            )}

                        </div>

                        {result.stance_unavailable_reason && (
                            <div className="text-amber-600 text-sm">
                                Stance analysis is currently unavailable: {result.stance_unavailable_reason}
                            </div>
                        )}

                        <PerspectiveOverview
                            left={result.bias_groups.left.length}
                            center={result.bias_groups.center.length}
                            right={result.bias_groups.right.length}
                        />

                        <PerspectiveSection
                            title="Left Perspective"
                            articles={result.bias_groups.left}
                        />

                        <PerspectiveSection
                            title="Center Perspective"
                            articles={result.bias_groups.center}
                        />

                        <PerspectiveSection
                            title="Right Perspective"
                            articles={result.bias_groups.right}
                        />

                    </>

                )}

            </div>

        </main>

    );

}
