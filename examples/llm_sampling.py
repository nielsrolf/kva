from kva import kva


inputs = [
    'Hello',
    'What is your name?',
    'How are you doing?'
]


def model(input, step):
    return f"I have been trained for {step} steps but still don't know how to respond to '{input}'"

if __name__ == "__main__":
    kva.init(run_id="Fake LLM Sampling")

    for step in range(100):
        kva.log(step=step, square=step**2)
        kva.log(loss=1/(step+1))

        if step % 10 == 0:
            for input in inputs:
                response = model(input, step)
                kva.log(input=input, output=response)
        
        