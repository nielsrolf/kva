from kva import kva, Folder


kva.init(run_id="Current CWD")

kva.log(cwd=Folder('frontend'))

kva.log(cwd=Folder('src'))

merged_folder = kva.get(run_id="Current CWD").latest('cwd')

src_folder = kva.get(run_id="Current CWD").latest('cwd', deep_merge=False)