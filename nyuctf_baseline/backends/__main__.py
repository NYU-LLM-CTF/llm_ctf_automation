from . import Backend

if __name__ == "__main__":
    # Print out the backends that are available and the models that they support
    for backend in Backend.classes():
        print(f"Supported models for {backend.NAME}:")
        print(''.join(f'  - {m}\n' for m in backend.get_models()))
