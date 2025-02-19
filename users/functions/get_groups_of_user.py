from fastapi import HTTPException
from db.database import conn as DbConnection, dbData


def get_group_of_user(uid):

    search_filter = f"(uid={uid})"

    DbConnection.search(
        dbData.get("BASE_DN"),
        search_filter,
        attributes=["telephoneNumber", "cn", "userPassword"],
    )

    if not DbConnection.entries:
        raise HTTPException(status_code=404, detail="E7")

    DbConnection.search(dbData.get("BASE_DN"), search_filter, attributes=["gidNumber"])
    for entry in DbConnection.entries:
        # now find group that its gid number is equal to entry.gidNumber
        second_search_filter = f"(gidNumber={entry.gidNumber})"
        DbConnection.search(
            dbData.get("BASE_DN"),
            second_search_filter,
            attributes=[
                "cn",
            ],
        )
        for group in DbConnection.entries:
            return group.cn
