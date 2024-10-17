import pandas as pd
import kva
import time


def get_dummy_df(text):
    df = pd.DataFrame([{
        'text': text,
        'row': i,
    } for i in range(20)])
    return df



if __name__ == "__main__":
    run = kva.init(run_id=f"Nested tables test - {time.time()}")

    kva.log(step=1)
    kva.log({'dummy_table': get_dummy_df('dummy text')})
    kva.log(step=2)
    kva.log({'dummy_table': get_dummy_df('updated text')})


    table = kva.Table(columns=['text', 'row'])
    for i in range(20):
        table.add_row(text='dummy text', row=i)

    kva.log({"wandb_like_table": table})


    print("dummy_table step=1")
    df1 = run.get(step=1).latest('dummy_table').as_df()
    print(df1)


    df1 = run.latest('dummy_table').as_df()
    print('dummy_table')
    print(df1)

    df2 = run.latest('wandb_like_table').as_df()
    print('wandb_like_table')
    print(df2)

    print(df1.equals(df2))



    data = run.latest(['dummy_table', 'wandb_like_table'], index='step')

    print(data)

    print("index", data.index)
    print("cols", data.columns)