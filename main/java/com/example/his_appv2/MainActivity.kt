package com.example.his_appv2

import android.content.Intent
import android.os.Bundle
import android.util.Log.d
import com.google.firebase.auth.FirebaseAuth


class MainActivity : BaseActivity(0) {
    private val TAG = "HomeActivity"
    private lateinit var mAuth: FirebaseAuth

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        setupBottomNavigation()
        d(TAG, "onCreate")
        mAuth = FirebaseAuth.getInstance()
    }

    override fun onStart() {
        super.onStart()
        if (mAuth.currentUser==null){
            startActivity(Intent(this, LoginActivity::class.java))
            finish()
        }
    }
}