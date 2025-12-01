'use client';

import { ErrorPage } from '@/components/pages/ErrorPage';

export default function CategoryError({
  error
}: {
  error: Error & { digest?: string };
}) {

  return <ErrorPage error={error} />;
}