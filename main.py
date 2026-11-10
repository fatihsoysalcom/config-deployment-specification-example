import json
import os

# --- Simulate Configuration Data (representing files on disk or in a CMDB) ---

# Base configuration that might be common across environments
base_config = {
    "APP_NAME": "MyWebApp",
    "VERSION": "1.0.0",
    "LOG_LEVEL": "INFO",
    "TIMEOUT_SECONDS": 30
}

# Staging environment specific overrides
staging_overrides = {
    "DEBUG": True,
    "DATABASE_URL": "sqlite:///./staging.db",
    "API_KEY": "DEV_KEY_STAGING",
    "LOG_LEVEL": "DEBUG"
}

# Production environment specific overrides
production_overrides = {
    "DEBUG": False,
    "DATABASE_URL": "postgresql://user:pass@prod-db.example.com:5432/myapp_prod",
    "API_KEY": os.getenv("PROD_API_KEY", "SECURE_PROD_KEY_DEFAULT"), # Should ideally come from ENV vars
    "TIMEOUT_SECONDS": 60,
    "CACHE_ENABLED": True
}

def merge_configs(base: dict, overrides: dict) -> dict:
    """Merges base configuration with environment-specific overrides."""
    merged = base.copy()
    merged.update(overrides)
    return merged

# --- Specification for Production Environment (implicit in validation logic) ---
# This is where the "spec" for a mechanical transfer (config deployment) lives.
# It defines what constitutes a "valid" production configuration.

def validate_production_config(config: dict) -> list:
    """
    Validates a configuration dictionary against production environment specifications.
    Returns a list of error messages if validation fails, empty list otherwise.
    """
    errors = []
    # SPEC RULE 1: Debug mode must be off in production
    if config.get("DEBUG", True): # Default to True if missing, to be safe
        errors.append("Production config must have 'DEBUG' set to False.")

    # SPEC RULE 2: Database URL must point to a production database
    db_url = config.get("DATABASE_URL")
    if not db_url or "prod" not in db_url.lower():
        errors.append("Production config 'DATABASE_URL' is missing or does not indicate a production database.")

    # SPEC RULE 3: API Key must be present and not a development key
    api_key = config.get("API_KEY")
    if not api_key or "DEV_KEY" in api_key:
        errors.append("Production config 'API_KEY' is missing or appears to be a development key.")
    
    # SPEC RULE 4: Cache must be enabled for performance
    if not config.get("CACHE_ENABLED", False):
        errors.append("Production config 'CACHE_ENABLED' must be True.")

    return errors

def deploy_config_to_target(config_to_apply: dict, target_env: str, dry_run: bool = True):
    """
    Simulates applying a given configuration to a target environment.
    This function embodies the "mechanical transfer" process,
    with crucial specification-driven validation for production.
    """
    print(f"--- Attempting to deploy configuration to {target_env} ---")

    print(f"\nConfiguration proposed for {target_env}:")
    print(json.dumps(config_to_apply, indent=2))

    if target_env == "production":
        print("\n--- Validating proposed configuration against Production Specification ---")
        validation_errors = validate_production_config(config_to_apply)
        if validation_errors:
            print("Validation FAILED! The following issues were found:")
            for error in validation_errors:
                print(f"  - {error}")
            print("\nDeployment ABORTED due to specification violations.")
            return
        else:
            print("Validation PASSED! Configuration meets production specifications.")
    else:
        print(f"\nNo strict validation rules defined for {target_env} in this example (only production is strict).")

    if dry_run:
        print(f"\n--- DRY RUN: Configuration for {target_env} would be applied. No changes made. ---")
    else:
        print(f"\n--- Applying configuration to {target_env}... (Simulated) ---")
        # In a real scenario, this would involve writing to files, updating databases, etc.
        print(f"Configuration successfully applied to {target_env}.")

    print(f"\n--- Deployment to {target_env} finished. ---")


if __name__ == "__main__":
    print("This script demonstrates why even 'mechanical transfers' need a specification.")
    print("It simulates deploying configuration, with validation rules acting as the 'spec'.")

    # Prepare configurations for different scenarios
    staging_final_config = merge_configs(base_config, staging_overrides)
    production_final_config = merge_configs(base_config, production_overrides)

    # Simulate a bad production config (e.g., someone copied staging config values by mistake)
    bad_production_config_attempt = merge_configs(base_config, {
        "DEBUG": True, # Violation 1: Debug mode on
        "DATABASE_URL": "sqlite:///./dev.db", # Violation 2: Dev database URL
        "API_KEY": "DEV_KEY_STAGING", # Violation 3: Dev API key
        "CACHE_ENABLED": False # Violation 4: Cache disabled
    })


    print("\n" + "="*80 + "\n")
    print("--- Scenario 1: Deploying a VALID production config (dry run) ---")
    deploy_config_to_target(config_to_apply=production_final_config, target_env="production", dry_run=True)

    print("\n" + "="*80 + "\n")

    print("--- Scenario 2: Attempting to deploy a BAD config to production (dry run) ---")
    deploy_config_to_target(config_to_apply=bad_production_config_attempt, target_env="production", dry_run=True)

    print("\n" + "="*80 + "\n")

    print("--- Scenario 3: Deploying a VALID production config (actual run) ---")
    deploy_config_to_target(config_to_apply=production_final_config, target_env="production", dry_run=False)

    print("\n" + "="*80 + "\n")

    print("--- Scenario 4: Deploying a staging config to staging (no strict validation in this example) ---")
    deploy_config_to_target(config_to_apply=staging_final_config, target_env="staging", dry_run=True)
