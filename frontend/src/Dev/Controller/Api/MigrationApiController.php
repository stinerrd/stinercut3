<?php

namespace App\Dev\Controller\Api;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use WouterJ\EloquentBundle\Facade\Schema;

#[Route('/api/dev/migrations')]
class MigrationApiController extends AbstractController
{
    private string $migrationsPath;

    public function __construct(string $projectDir)
    {
        $this->migrationsPath = $projectDir . '/migrations';
    }

    #[Route('', name: 'api_dev_migrations_list', methods: ['GET'])]
    public function list(): JsonResponse
    {
        if (!$this->isDev()) {
            return $this->devOnlyResponse();
        }

        $migrations = $this->getMigrations();

        return new JsonResponse([
            'success' => true,
            'data' => array_map(fn($m) => [
                'name' => $m['name'],
                'table' => $m['table'],
            ], $migrations),
        ]);
    }

    #[Route('/reset/{identifier}', name: 'api_dev_migrations_reset', methods: ['POST'])]
    public function reset(string $identifier): JsonResponse
    {
        if (!$this->isDev()) {
            return $this->devOnlyResponse();
        }

        // Accept either table name (e.g., "setting") or migration name (e.g., "2025_11_29_100000_create_setting_table")
        $migration = $this->findMigration($identifier);

        if (!$migration) {
            return new JsonResponse([
                'success' => false,
                'error' => "Migration '$identifier' not found. Use table name (e.g., 'setting') or migration name.",
            ], Response::HTTP_NOT_FOUND);
        }

        try {
            // Drop the table
            Schema::dropIfExists($migration['table']);

            // Re-run the migration
            $class = require $migration['path'];
            $class->up();

            return new JsonResponse([
                'success' => true,
                'message' => "Table '{$migration['table']}' dropped and migration re-executed",
                'migration' => $migration['name'],
            ]);
        } catch (\Throwable $e) {
            return new JsonResponse([
                'success' => false,
                'error' => $e->getMessage(),
            ], Response::HTTP_INTERNAL_SERVER_ERROR);
        }
    }

    private function isDev(): bool
    {
        return $this->getParameter('kernel.environment') === 'dev';
    }

    private function devOnlyResponse(): JsonResponse
    {
        return new JsonResponse([
            'success' => false,
            'error' => 'This endpoint is only available in development environment',
        ], Response::HTTP_FORBIDDEN);
    }

    private function getMigrations(): array
    {
        $files = glob($this->migrationsPath . '/*.php');
        sort($files);

        $migrations = [];
        foreach ($files as $file) {
            $name = basename($file, '.php');
            // Extract table name from migration name (e.g., "create_setting_table" -> "setting")
            if (preg_match('/create_(\w+)_table/', $name, $matches)) {
                $migrations[] = [
                    'name' => $name,
                    'table' => $matches[1],
                    'path' => $file,
                ];
            }
        }

        return $migrations;
    }

    private function findMigration(string $identifier): ?array
    {
        foreach ($this->getMigrations() as $migration) {
            // Match by table name or migration name
            if ($migration['table'] === $identifier || $migration['name'] === $identifier) {
                return $migration;
            }
        }

        return null;
    }
}
