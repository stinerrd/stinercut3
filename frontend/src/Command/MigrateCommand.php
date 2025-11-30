<?php

namespace App\Command;

use Illuminate\Database\Capsule\Manager as Capsule;
use Symfony\Component\Console\Attribute\AsCommand;
use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Output\OutputInterface;
use WouterJ\EloquentBundle\Facade\Schema;
use WouterJ\EloquentBundle\Facade\Db;

#[AsCommand(
    name: 'migrate',
    description: 'Run database migrations',
)]
class MigrateCommand extends Command
{
    public function execute(InputInterface $input, OutputInterface $output): int
    {
        $output->writeln('<info>Running migrations...</info>');

        $migrationPath = $this->getApplication()->getKernel()->getProjectDir() . '/migrations';
        $migrations = glob($migrationPath . '/*.php');
        sort($migrations);

        foreach ($migrations as $migration) {
            $class = include $migration;
            if (is_object($class) && method_exists($class, 'up')) {
                $name = basename($migration);
                $output->write("  <comment>$name</comment> ... ");
                try {
                    $class->up();
                    $output->writeln('<info>OK</info>');
                } catch (\Exception $e) {
                    $output->writeln('<error>ERROR</error>');
                    $output->writeln('  ' . $e->getMessage());
                }
            }
        }

        $output->writeln('<info>Migrations completed!</info>');
        return Command::SUCCESS;
    }
}
