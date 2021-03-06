from typing import Iterable

from gen_base import gen_runner, gen_typing
from gen_from_tests.gen import generate_from_tests
from importlib import reload, import_module
from eth2spec.config import config_util
from eth2spec.phase0 import spec as spec_phase0
from eth2spec.phase1 import spec as spec_phase1
from eth2spec.test.context import PHASE0, PHASE1
from eth2spec.utils import bls


def create_provider(fork_name: str, handler_name: str,
                    tests_src_mod_name: str, config_name: str) -> gen_typing.TestProvider:
    def prepare_fn(configs_path: str) -> str:
        config_util.prepare_config(configs_path, config_name)
        reload(spec_phase0)
        reload(spec_phase1)
        bls.use_milagro()
        return config_name

    def cases_fn() -> Iterable[gen_typing.TestCase]:
        tests_src = import_module(tests_src_mod_name)
        return generate_from_tests(
            runner_name='epoch_processing',
            handler_name=handler_name,
            src=tests_src,
            fork_name=fork_name,
        )

    return gen_typing.TestProvider(prepare=prepare_fn, make_cases=cases_fn)


if __name__ == "__main__":
    phase_0_mods = {key: 'eth2spec.test.phase0.epoch_processing.test_process_' + key for key in [
        'justification_and_finalization',
        'rewards_and_penalties',
        'registry_updates',
        'slashings',
        'eth1_data_reset',
        'effective_balance_updates',
        'slashings_reset',
        'randao_mixes_reset',
        'historical_roots_update',
        'participation_record_updates',
    ]}
    phase_1_mods = {**{key: 'eth2spec.test.phase1.epoch_processing.test_process_' + key for key in [
        'reveal_deadlines',
        'challenge_deadlines',
        'custody_final_updates',
    ]}, **phase_0_mods}  # also run the previous phase 0 tests (but against phase 1 spec)

    gen_runner.run_generator(f"epoch_processing", [
        create_provider(PHASE0, key, mod_name, 'minimal') for key, mod_name in phase_0_mods.items()
    ])
    gen_runner.run_generator(f"epoch_processing", [
        create_provider(PHASE0, key, mod_name, 'mainnet') for key, mod_name in phase_0_mods.items()
    ])
    gen_runner.run_generator(f"epoch_processing", [
        create_provider(PHASE1, key, mod_name, 'minimal') for key, mod_name in phase_1_mods.items()
    ])
    gen_runner.run_generator(f"epoch_processing", [
        create_provider(PHASE1, key, mod_name, 'mainnet') for key, mod_name in phase_1_mods.items()
    ])
